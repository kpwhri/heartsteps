import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";

declare var cordova;
declare var window;

@Injectable()
export class BrowserService {

    constructor(
        private platform: Platform
    ) {}

    open(url: string) {
        if (this.platform.is('ios') || this.platform.is('android')) {
            cordova.InAppBrowser.open(url, '_system');
        } else {
            window.open(url, '_blank');
        }
    }
}