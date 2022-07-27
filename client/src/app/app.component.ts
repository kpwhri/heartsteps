import { Component } from '@angular/core';
import { ParticipantService, Participant } from '@heartsteps/participants/participant.service';
import { AppStatusService, APP_STATUS } from '@infrastructure/app-status.service';
import { Router, NavigationEnd } from '@angular/router';
import { AppService } from './app.service';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { BackgroundMode } from '@ionic-native/background-mode/ngx';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private appStatusService: AppStatusService,
        private participantService: ParticipantService,
        private appService: AppService,
        private router: Router,
        private backgroundMode: BackgroundMode
    ) {
        console.log('src', 'app', 'app.component.ts', 'MyApp', 'constructor');
        // subscribe to the participant service to get the participant info who is looking at the screen right now
        this.appStatusService.getStatus()
            .then((status) => {
                if (status == APP_STATUS.AUTHENTICATED) {
                } else if (status == APP_STATUS.NOT_AUTHENTICATED) {
                }
            });

        console.log('src', 'app', 'app.component.ts', 'MyApp', 'constructor', 'status', status);
        this.participantService.participant.subscribe((participant) => {
            this.updateRoute(participant);
        });

        // trying to hijacking the screen if the participant is fetchable
        this.router.events
            .filter((event) => event instanceof NavigationEnd)  // even after the routing is finished, if we're still in the '/', then
            .subscribe((event: NavigationEnd) => {
                if (event.url == "/") {
                    console.log('src', 'app', 'app.component.ts', 'MyApp', '1');
                    this.participantService.get()   // try directly to get the participant info
                        .then((participant) => {
                            console.log('src', 'app', 'app.component.ts', 'MyApp', '2');
                            this.updateRoute(participant);  // and use that info to update the screen (branching to proper screen depending on the participant status)
                        });
                }
            })

        console.log('src', 'app', 'app.component.ts', 'MyApp', '3');
        platform.ready()    // if the platform is ready (device, resource)
            .then(() => {
                console.log('src', 'app', 'app.component.ts', 'MyApp', '4');
                return this.appService.setup()  // tries to initialize all app services
            })
            .then(() => {                   // after that
                console.log('src', 'app', 'app.component.ts', 'MyApp', '5');
                statusBar.styleDefault();   // make the status bar appear
                splashScreen.hide();        // make the splashScreen go away
                this.backgroundMode.enable();   // allow background app refresh function execution
            });




    }

    private updateRoute(participant: Participant) {
        // participant status process:
        // no participant | not loaded | not setup | not baselineCompleted | everything is set
        // welcome        | loading    | onboard   | baseline              | home/dashboard
        console.log('src', 'app', 'app.component.ts', 'MyApp', 'updateRoute', '1');
        if (this.router.url === "/") {
            console.log('src', 'app', 'app.component.ts', 'MyApp', 'updateRoute', '2');
            if (participant && participant.isLoaded && participant.isSetup && participant.isBaselineComplete) {
                this.router.navigate(['home', 'dashboard']);
            } else if (participant && participant.isLoaded && participant.isSetup) {
                this.router.navigate(['baseline']);
            } else if (participant && participant.isLoaded) {
                this.router.navigate(['onboard'])
            } else if (participant) {
                this.router.navigate(['loading']);
            } else {
                this.router.navigate(['welcome']);
            }
        }
    }

}
