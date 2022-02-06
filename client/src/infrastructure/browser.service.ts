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
        console.log('BrowserService.open():', 1, url);
        if (this.platform.is('cordova')) {
            console.log('BrowserService.open():', 2);
            return this.checkSafariAvailable()
            .then(() => {
                console.log('BrowserService.open():', 3);
                return this.openInSafari(url)
            })
            .catch(() => {
                console.log('BrowserService.open():', 4);
                try {
                    this.navigateTo(url);
                    return Promise.resolve(true);
                } catch (e) {
                    console.log('BrowserService.open():', 5);
                    return Promise.reject("Opening browser not supported")
                }
                
            })
        } else {
            console.log('BrowserService.open():', 5);
            this.navigateTo(url);
            console.log('BrowserService.open():', 6);
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
        console.log('BrowserService.checkSafariAvailable():', 1);
        return new Promise((resolve, reject) => {
            console.log('BrowserService.checkSafariAvailable():', 2);
            SafariViewController.isAvailable((available) => {
                console.log('BrowserService.checkSafariAvailable():', 3);
                if(available) {
                    console.log('BrowserService.checkSafariAvailable():', 4);
                    resolve();
                } else {
                    console.log('BrowserService.checkSafariAvailable():', 5);
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
