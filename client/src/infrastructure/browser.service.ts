import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { SafariViewController } from '@ionic-native/safari-view-controller';

// tslint:disable-next-line:no-unused-variable
declare var cordova;

@Injectable()
export class BrowserService {

    constructor(
        private platform: Platform,
        private safariViewController: SafariViewController
    ) {}

    public open(url: string): Promise<boolean> {
        if (this.platform.is('cordova')) {
            console.log('Browser Server', 'Is Cordova');
            return this.checkSafariAvailable()
            .then(() => {
                console.log('Browser Server', 'Open is safari');
                return this.openInSafari(url)
            })
            .catch(() => {
                console.log('Browser Service', 'Did not ooen');
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
            this.safariViewController.hide();
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.resolve(true);
        })
    }

    public open_external(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            if (this.platform.is('ios') || this.platform.is('android')) {
                window.open(url, '_system');
            } else {
                window.open(url, '_blank');
            }
            resolve(true);
        })
    }

    private checkSafariAvailable(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.safariViewController.isAvailable()
            .then((available) => {
                if(available) {
                    resolve(true);
                } else {
                    reject();
                }
            })
            .catch(() => {
                reject();
            });
        });
    }

    private openInSafari(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            this.safariViewController.show({
                url: url
            })
            .subscribe((result) => {
                console.log(result)
                if(result.event === 'closed') {
                    resolve();
                }
            });
        });
    }

    public openAndWait(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            const childWindow: Window = window.open(url);
            const interval = setInterval(function() {
                if(childWindow.closed) {
                    resolve();
                    clearInterval(interval);
                }
            }, 500);
        });
    }

    private navigateTo(url: string) {
        window.location.assign(url);
    }
}
