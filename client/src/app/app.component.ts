import { Component } from '@angular/core';
import { ParticipantService, Participant } from '@heartsteps/participants/participant.service';
import { Router, NavigationEnd } from '@angular/router';
import { AppService } from './app.service';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private participantService:ParticipantService,
        private appService: AppService,
        private router: Router
    ) {
        // subscribe to the participant service to get the participant info who is looking at the screen right now
        this.participantService.participant.subscribe((participant) => {
            this.updateRoute(participant);
        });

        this.router.events
        .filter((event) => event instanceof NavigationEnd)  // even after the routing is finished, if we're still in the '/', then
        .subscribe((event: NavigationEnd) => {
            if (event.url == "/") { 
                this.participantService.get()   // try directly to get the participant info
                .then((participant) => {
                    this.updateRoute(participant);  // and use that info to update the screen (branching to proper screen depending on the participant status)
                });
            }
        })
        
        platform.ready()    // if the platform is ready (device, resource)
        .then(() => {
            return this.appService.setup()  // go to the initial app service setup logic
        })
        .then(() => {                   // after that
            statusBar.styleDefault();   // make the status bar appear
            splashScreen.hide();        // make the splashScreen go away
        });
    }

    private updateRoute(participant: Participant) {
        // participant status process:
        // no participant | not loaded | not setup | not baselineCompleted | everything is set
        // welcome        | loading    | onboard   | baseline              | home/dashboard
        if(this.router.url === "/") { 
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
