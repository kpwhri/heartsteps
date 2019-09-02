import { Component, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";
import { FormGroup, FormControl } from "@angular/forms";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ParticipantInformationService } from "@heartsteps/participants/participant-information.service";

@Component({
    selector: 'heartsteps-notification-page',
    templateUrl: './notification.page.html'
})
export class NotificationPage implements OnInit {
    private notification: Message;

    public title: string;
    public body: string;

    public loading: boolean;
    public ratingForm: FormGroup;
    public isStaff: boolean;

    constructor(
        private router: Router,
        private activatedRoute: ActivatedRoute,
        private messageService: MessageService,
        private heartstepsServer: HeartstepsServer,
        private participantInformationService: ParticipantInformationService
    ) {}

    ngOnInit() {
        this.activatedRoute.paramMap.subscribe((paramMap) => {
            this.loading = true;
            const notificationId: string = paramMap.get('notificationId');
            this.messageService.getMessage(notificationId)
            .then((notification) => {
                this.loading = false;
                this.notification = notification;
                this.title = this.notification.title;
                this.body = this.notification.body;

                if(this.notification.context.randomizationId) {
                    this.setupRatingForm();
                    this.updateStaffStatus();
                } else {
                    this.ratingForm = null;
                }
            }) 
            this.messageService.getMessage(notificationId)
            .then((notification) => {
            });
        });
    }

    public dismiss() {
        this.notification.engaged();
        this.router.navigate(['']);
    }

    private updateStaffStatus() {
        this.participantInformationService.isStaff()
        .then(() => {
            this.isStaff = true;
        })
        .catch(() => {
            this.isStaff = false;
        });
    }

    private setupRatingForm() {
        this.ratingForm = new FormGroup({
            liked: new FormControl(),
            comments: new FormControl()
        });
    }

    public saveRating() {
        const randomizationId = this.notification.context.randomizationId;
        if(randomizationId) {
            this.heartstepsServer.post('activity-suggestions/' + randomizationId +'/rating', this.ratingForm.value)
            .catch(() => {
                // nothing
            })
            .then(() => {
                this.dismiss();
            })
        } else {
            this.dismiss();
        }
    }

}
