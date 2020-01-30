import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { AuthorizationService } from "@infrastructure/authorization.service";
import { Router, NavigationEnd } from "@angular/router";

declare var process: {
    env: {
        BUILD_PLATFORM: string,
        BUILD_VERSION: string,
        BUILD_NUMBER: string
    }
}

@Injectable()
export class AnalyticsService {

    private platform: string;
    private version: string; 
    private build: string;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private authorizationService: AuthorizationService,
        private router: Router
    ) {
        this.build = process.env.BUILD_NUMBER;
        this.platform = process.env.BUILD_PLATFORM;
        this.version = process.env.BUILD_VERSION;
    }

    public setup(): Promise<void> {
        return this.setupRouter()
        .then(() => {
            return undefined;
        });
    }

    private setupRouter():Promise<boolean> {
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
        return Promise.resolve(true);
    }

    public trackPageView(uri:string):Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .then(() => {
            return this.heartstepsServer.post('/page-views', {
                uri: uri,
                time: new Date().toISOString(),
                platform: this.platform,
                version: this.version,
                build: this.build
            });
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

}
