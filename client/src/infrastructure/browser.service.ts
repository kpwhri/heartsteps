import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { SafariViewController } from '@ionic-native/safari-view-controller';

declare var cordova;

@Injectable()
export class BrowserService {

    constructor(
        private platform: Platform,
        private safariViewController: SafariViewController
    ) {}

    public open(url: string): Promise<boolean> {
        if (this.platform.is('ios') || this.platform.is('android')) {
            return this.checkSafariAvailable()
            .then(() => {
                return this.openInSafari(url)
            })
            .catch(() => {
                return Promise.reject("Opening browser not supported")
            })
        } else {
            return this.openInBrowser(url)
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
        })
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

    private openInBrowser(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            const childWindow: Window = window.open(url)
            const interval = setInterval(function() {
                if(childWindow.closed) {
                    resolve();
                    clearInterval(interval);
                }
            }, 500);
        });
    }
}