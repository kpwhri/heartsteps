import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { AuthorizationService } from "@infrastructure/authorization.service";
import { Router, NavigationEnd } from "@angular/router";
import { StorageService } from "@infrastructure/storage.service";

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

    private delayUploadTimeout: any;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private authorizationService: AuthorizationService,
        private router: Router,
        private storage: StorageService
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
            const pageView = this.createPageView(uri);
            return this.storePageView(pageView);
        })
        .then(() => {
            this.delayUpload();
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    public uploadPageView(): Promise<void> {
        return this.storage.get('page-views')
        .then((pageViews) => {
            return this.heartstepsServer.post('page-views', pageViews)
        })
        .then(() => {
            this.storage.remove('page-views');
        });
    }

    private delayUpload() {
        if (this.delayUploadTimeout) clearTimeout(this.delayUploadTimeout);
        this.delayUploadTimeout = setTimeout(() => {
            this.uploadPageView()
        }, 1000);
    }

    private createPageView(uri: string): any {
        return {
            uri: uri,
            time: new Date().toISOString(),
            platform: this.platform,
            version: this.version,
            build: this.build
        }
    }

    private storePageView(pageView:any):Promise<void> {
        return this.storage.get('page-views')
        .catch(() => {
            return [];
        })
        .then((pageViews) => {
            if (!Array.isArray(pageViews)) {
                pageViews = []
            }
            pageViews.push(pageView);
            return this.storage.set('page-views', pageViews);
        });
    }

}
