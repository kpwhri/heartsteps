import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { InAppBrowser, InAppBrowserObject } from '@ionic-native/in-app-browser';
import { SafariViewController } from '@ionic-native/safari-view-controller';

@Injectable()
export class BrowserService {

    constructor(
        private platform: Platform,
        private safariViewController: SafariViewController,
        private inAppBrowser: InAppBrowser
    ) {}

    open(url: string): Promise<boolean> {
        if (this.platform.is('ios') || this.platform.is('android')) {
            return this.checkSafariAvailable()
            .then(() => {
                return this.openInSafari(url)
            })
            .catch(() => {
                return this.openInAppBrowser(url)
            })
        } else {
            return this.openInBrowser(url)
        }
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
                if(result.event === 'closed') {
                    resolve();
                }
            });
        });
    }

    private openInAppBrowser(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            const browser: InAppBrowserObject = this.inAppBrowser.create(url, "_system");

            browser.on('close').subscribe(() => {
                resolve(true);
            });
        });
    }

    private openInBrowser(url: string): Promise<boolean> {
        return new Promise((resolve) => {
            const browser: Window = window.open(url)

            browser.addEventListener('close', () => {
                console.log("closing browser")
                resolve();
            })
        });
    }
}