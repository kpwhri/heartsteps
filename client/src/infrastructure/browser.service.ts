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

    open(url: string): Promise<boolean> {
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

    close(): Promise<boolean> {
        return this.checkSafariAvailable()
        .then(() => {
            this.safariViewController.hide();
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.resolve(true);
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