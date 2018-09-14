import { Component, ViewChild } from '@angular/core';
import { Platform, Nav } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { WelcomePage } from '@pages/welcome/welcome';
import { ParticipantService } from '@heartsteps/participant.service';
import { OnboardPage } from '@pages/onboard/onboard';
import { HomePage } from '@pages/home/home';
import { AuthorizationService } from '@infrastructure/authorization.service';
import { NotificationService } from '@app/notification.service';

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
        private participant:ParticipantService,
        private authorizationService:AuthorizationService,
        notificationService: NotificationService
    ) {
        platform.ready()
        .then(() => {
            this.setNavAuthGuard()
            this.participant.onChange().subscribe((participant: any) => {
                this.updateRootPage(participant);
            })
            return this.participant.update()
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
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

    updateRootPage(participant:any) {
        let rootPage: any = WelcomePage;
        if (participant.enrolled) {
            rootPage = OnboardPage;
        }
        if (participant.profileComplete) {
            rootPage = HomePage;
        }
        this.nav.setRoot(rootPage);
        this.nav.popToRoot();
    }
}

