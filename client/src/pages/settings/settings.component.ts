import { Component } from "@angular/core";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { Router } from "@angular/router";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { LoadingService } from "@infrastructure/loading.service";
import { AntiSedentaryService } from "@heartsteps/anti-sedentary/anti-sedentary.service";
import { Platform } from "ionic-angular";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { Message } from "@heartsteps/notifications/message.model";
import { ActivitySurveyService } from "@heartsteps/activity-surveys/activity-survey.service";
import { MessageService } from "@heartsteps/notifications/message.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

declare var process: {
    env: {
        BUILD_VERSION: string,
        BUILD_DATE: string
    }
}

@Component({
    templateUrl: 'settings.component.html',
    selector: 'pages-settings-component'
})
export class SettingsComponent {

    public staffParticipant: boolean = false;
    public buildVersion: string = process.env.BUILD_VERSION;
    public buildDate: string = process.env.BUILD_DATE;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private messageService: MessageService,
        private activitySurveyService: ActivitySurveyService,
        private walkingSuggestionService:WalkingSuggestionService,
        private enrollmentService:EnrollmentService,
        private router:Router,
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController,
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private antiSedentaryService: AntiSedentaryService,
        private participantService: ParticipantService,
        private platform: Platform
    ) {
        this.participantService.participant
        .filter(participant => participant !== undefined)
        .first()
        .subscribe((participant) => {
            this.staffParticipant = participant.staff;
        })
    }

    public goBack() {
        this.router.navigate(['/'])
        .then(() => {
            return this.participantService.update();
        });
    }

    public testWalkingSuggestion() {
        this.loadingService.show('Requesting walking suggestion message');
        this.walkingSuggestionService.createTestDecision()
        .catch(() => {
            this.alertDialog.show('Error sending test message');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public testActivitySurvey() {
        this.loadingService.show("Requesting activity survey");
        this.activitySurveyService.sendTestActivitySurvey()
        .then((message) => {
            if(!this.platform.is('cordova')) {
                return this.openMessage(message);
            }
        })
        .catch((error) => {
            this.alertDialog.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }


    public testWalkingSuggestionSurvey() {
        this.loadingService.show("Requesting walking suggestion survey");
        this.heartstepsServer.post('/walking-suggestion-survey/test', {})
        .then((data) => {
            return this.loadMessage(data.notificationId);
        })
        .then(() => {
            this.loadingService.dismiss();
        })
        .catch((error) => {
            this.loadingService.dismiss();
            this.alertDialog.show(error);
        });
    }

    private loadMessage(notificationId): Promise<void> {
        return this.messageService.loadMessage(notificationId)
        .then((message) => {
            if(!this.platform.is('cordova')) {
                return this.openMessage(message);
            }
        });
    }

    public testAntisedentaryMessage() {
        this.loadingService.show("Requesting anti-sedentary message");
        this.antiSedentaryService.sendTestMessage()
        .then((message) => {
            if(!this.platform.is('cordova')) {
                return this.openMessage(message);
            }
        })
        .catch(() => {
            this.alertDialog.show('Error sending anti-sedentary message');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    private openMessage(message: Message) {
        message.received();
        return this.router.navigate(['notification', message.id])
        .then(() => {
            message.displayed();
        });
    }

    private requestMorningMessage() {
        this.loadingService.show("Requesting morning message");
        this.morningMessageService.requestNotification()
        .catch(() => {
            this.alertDialog.show("Error sending morning message");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    private loadMorningMessage() {
        this.loadingService.show('Loading morning message')
        this.morningMessageService.load()
        .catch(() => {
            this.alertDialog.show("Error loading morning message");
        })
        .then(() => {
            this.loadingService.dismiss();
            this.router.navigate(['morning-survey']);
        });
    }

    public testMorningMessage() {
        if(this.platform.is('cordova')) {
            this.requestMorningMessage();
        } else {
            this.loadMorningMessage();
        }
    }

    private requestWeeklySurvey() {
        this.loadingService.show("Requesting weekly survey");
        this.weeklySurveyService.testReflectionNotification()
        .catch(() => {
            this.alertDialog.show("Error sending weekly survey");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    private loadWeeklySurvey() {
        this.loadingService.show("Loading weekly survey");
        this.weeklySurveyService.testReflection()
        .catch(() => {
            this.alertDialog.show("Error loading weekly survey");
        })
        .then(() => {
            this.loadingService.dismiss();
            this.router.navigate(['weekly-survey']);
        })
    }

    public testWeeklySurveyMessage() {
        if(this.platform.is('cordova')) {
            this.requestWeeklySurvey();
        } else {
            this.loadWeeklySurvey();
        }
    }

    public logout() {
        this.loadingService.show('Logging out');
        this.enrollmentService.unenroll()
        .then(() => {
            this.router.navigate(['welcome']);
        })
        .catch((error) => {
            console.error('Settings page, logout:', error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public editContactInformation() {
        this.router.navigate([{
            outlets: {
                modal: ['settings','contact'].join('/')
            }
        }]);
    }

    public editPlaces() {
        this.router.navigate([{
            outlets: {
                modal: ['settings','places'].join('/')
            }
        }]);
    }

    public editWeeklyReflectionTime() {
        this.router.navigate([{
            outlets: {
                modal: ['settings','reflection-time'].join('/')
            }
        }]);
    }

    public editWeeklyGoal() {
        this.router.navigate([{
            outlets: {
                modal: ['settings','weekly-goal'].join('/')
            }
        }]);
    }

    public editDailyTimes() {
        this.router.navigate([{
            outlets: {
                modal: ['settings','suggestion-times'].join('/')
            }
        }]);
    }

    public testBaselineWeekPage() {
        this.router.navigate(['baseline'])
    }

    public editFitbitAuthorization() {
        this.router.navigate([{
            outlets: {
                modal: ['settings', 'fitbit-authorization'].join('/')
            }
        }])
    }

    public editFitbitWatch() {
        this.router.navigate([{
            outlets: {
                modal: ['settings', 'fitbit-watch'].join('/')
            }
        }])
    }
} 