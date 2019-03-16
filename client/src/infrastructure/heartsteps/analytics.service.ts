import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { AuthorizationService } from "@infrastructure/authorization.service";
import { Router, NavigationEnd } from "@angular/router";

@Injectable()
export class AnalyticsService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private authorizationService: AuthorizationService,
        private router: Router
    ) {}

    public setup() {
        this.setupRouter();
    }

    private setupRouter() {
        this.router.events
        .filter((event) => event instanceof NavigationEnd)
        .subscribe((event:NavigationEnd) => {
            const modalStr = '(modal:';
            const modalPosition = event.url.indexOf(modalStr);
            if(modalPosition >= 0) {
                let uri = event.url.substring(modalPosition + modalStr.length, event.url.length-1);
                this.trackPageView('/' + uri);
            } else {
                this.trackPageView(event.url);
            }
        });
    }

    public trackPageView(uri:string):Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .then(() => {
            return this.heartstepsServer.post('/page-views', [{
                uri: uri,
                time: new Date().toISOString()
            }]);
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

}
