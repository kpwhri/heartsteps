import { Injectable, EventEmitter } from "@angular/core";
import { Platform } from "ionic-angular";

declare var SafariViewController:any;

@Injectable()
export class BrowserService {

    public opened:EventEmitter<void> = new EventEmitter();
    public closed:EventEmitter<void> = new EventEmitter();

    constructor(
        private platform: Platform
    ) {}

    public open(url: string): Promise<boolean> {
        if (this.platform.is('cordova')) {
            return this.checkSafariAvailable()
            .then(() => {
                return this.openInSafari(url)
            })
            .catch(() => {
                return Promise.reject("Opening browser not supported")
            })
        } else {
            this.navigateTo(url);
            return Promise.resolve(true);
        }
    }

    public close(): Promise<boolean> {
        return this.checkSafariAvailable()
        .then(() => {
            SafariViewController.hide();
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.resolve(true);
        })
    }

    private checkSafariAvailable(): Promise<void> {
        return new Promise((resolve, reject) => {
            SafariViewController.isAvailable((available) => {
                if(available) {
                    resolve();
                } else {
                    reject('Safari not available');
                }
            })
        });
    }

    private openInSafari(url: string): Promise<boolean> {
        SafariViewController.show({
            url: url
        }, (result) => {
            if (result.event == 'opened') {
                this.opened.emit();
            }
            if (result.event === 'closed') {
                this.closed.emit();
            }
        }, (error) => {
            console.log('Safari error', error);
        });
        return Promise.resolve(true);
    }
    
    private navigateTo(url: string) {
        window.location.assign(url);
    }
}
