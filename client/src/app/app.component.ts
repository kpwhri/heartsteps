import { Component, ViewChild } from '@angular/core';
import { Platform, Nav, ModalController } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { WelcomePage } from '@pages/welcome/welcome';
import { HeartstepsNotifications } from '@heartsteps/heartsteps-notifications.service';
import { ParticipantService } from '@heartsteps/participant.service';
import { OnboardPage } from '@pages/onboard/onboard';
import { HomePage } from '@pages/home/home';
import { AuthorizationService } from '@infrastructure/authorization.service';
import { NotificationPane } from './notification';
import { Geolocation } from '@ionic-native/geolocation';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {
    @ViewChild(Nav) nav:Nav
    rootPage:any;

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private modalCtrl:ModalController,
        private notifications:HeartstepsNotifications,
        private participant:ParticipantService,
        private authorizationService:AuthorizationService,
        private geolocation:Geolocation,
        private heartstepsServer:HeartstepsServer
    ) {
        platform.ready()
        .then(() => {
            this.setNavAuthGuard()
            this.setParticipantChange()

            this.participant.update()

            this.notifications.onMessage().subscribe((message:any) => {
                this.showMessage(message.body);
            });

            this.notifications.onDataMessage().subscribe((payload:any) => {
                console.log("got data message...")
                if(payload.type == 'get_context' && payload.decision_id) {
                    this.geolocation.getCurrentPosition().then((position:Position) => {
                        this.heartstepsServer.post('/decisions/'+payload.decision_id, {
                            location: {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            }
                        })
                    })
                }
            })

            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    showMessage(message:string) {
        let modal = this.modalCtrl.create(NotificationPane, {
            message: message
        }, {
            showBackdrop: true,
            enableBackdropDismiss: true,
            cssClass: 'heartsteps-message-modal'
        })
        modal.present()
    }

    setNavAuthGuard() {
        this.nav.viewWillEnter.subscribe(() => {
            return this.authorizationService.isAuthorized()
            .catch(() => {
                const currentRoot = this.nav.first();
                if(currentRoot.component !== WelcomePage) {
                    this.nav.setRoot(WelcomePage);
                    this.nav.popToRoot();
                }
            });
        });
    }

    setParticipantChange() {
        this.participant.onChange().subscribe(() => {
            this.setParticipantRoot()
            .then(() => {
                this.nav.popToRoot();
            })
        });
    }

    setParticipantRoot():Promise<any> {
        return this.participant.hasCompleteProfile()
        .then(() => {
            this.nav.setRoot(HomePage)
        })
        .catch(() => {
            return this.participant.isEnrolled()
            .then(() => {
                this.nav.setRoot(OnboardPage)
                return Promise.resolve()
            })
            .catch(() => {
                this.nav.setRoot(WelcomePage)
                return Promise.resolve()
            })
        })
    }
}

