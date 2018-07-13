import { Component, ViewChild } from '@angular/core';
import { Platform, Nav, ModalController } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { WelcomePage } from '../pages/welcome/welcome';
import { HeartstepsNotifications } from '../heartsteps/heartsteps-notifications.service';
import { ParticipantService } from '../heartsteps/participant.service';
import { OnboardPage } from '../pages/onboard/onboard';
import { HomePage } from '../pages/home/home';
import { AuthorizationService } from '../infrastructure/authorization.service';
import { NotificationPane } from './notification';

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
        private authorizationService:AuthorizationService
    ) {
        platform.ready()
        .then(() => {
            this.setNavAuthGuard()
            this.setParticipantChange()

            return this.participant.refresh()     
        })
        .then(() => {
            this.notifications.onMessage().subscribe((message:string) => {
                this.showMessage(message);
            });

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
            if(this.participant.isOnboarded()) {
                this.nav.setRoot(HomePage);
            } else if(this.participant.isEnrolled()) {
                this.nav.setRoot(OnboardPage); 
            } else {
                this.nav.setRoot(WelcomePage);
            }
            this.nav.popToRoot();
        });
    }
}

