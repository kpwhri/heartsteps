import { Injectable, NgZone } from "@angular/core";
import { Subject } from "rxjs";

declare var cordova:any;

declare var window: any;
window.skipLocalNotificationReady = true;

@Injectable()
export class LocalNotificationService {

    public clicked:Subject<string> = new Subject();

    constructor(
        private zone: NgZone
    ) {}

    public setup() {
        if (cordova) {
            this.setupNotificationListener();
            if(cordova.plugins.notification.local.fireQueuedEvents) {
                cordova.plugins.notification.local.fireQueuedEvents();
            }
        }
    }

    public disable() {

    }

    public enable(): Promise<boolean> {
        if(cordova) {
            return this.requestPermission();
        } else {
            return Promise.resolve(true);
        }
    }

    public isEnabled():Promise<boolean> {
        if(cordova) {
            return this.hasPermission();
        } else {
            return Promise.resolve(true);
        }
    }

    public create(id: string, text:string):Promise<boolean> {
        if (cordova) {
            return this.createNotification(id, text)
            .then(() => {
                return true;
            });
        } else {
            return Promise.resolve(true);
        }
    }

    public remove(id: string):Promise<boolean> {
        return Promise.resolve(true);
    }

    private hasPermission(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            cordova.plugins.notification.local.hasPermission(function(granted) {
                if(granted) {
                    resolve(true);
                } else {
                    reject('No permission');
                }
            })
        })
    }

    private requestPermission(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            cordova.plugins.notification.local.requestPermission(function(granted) {
                if(granted) {
                    resolve(true);
                } else {
                    reject('Permission rejected');
                }
            });
        })
    }

    private createNotification(id: string, text: string):Promise<boolean> {
        return this.getNotificationId()
        .then((notificationId) => {
            cordova.plugins.notification.local.schedule({
                id: notificationId,
                text: text,
                data: {
                    messageId: id
                }
            })
            return Promise.resolve(true);
        });
    }

    private getNotificationId():Promise<number> {
        return this.getExistingNotificationIds()
        .then((existingIds) => {
            return this.randomNumber(existingIds);
        });
    }

    private getExistingNotificationIds():Promise<Array<number>> {
        return new Promise((resolve, reject) => {
            cordova.plugins.notification.local.getIds(function(ids:Array<number>) {
                resolve(ids);
            });
        });
    }

    private randomNumber(existingIds:Array<number>):number {
        const number:number = Math.round(Math.random() * 1000);
        if(existingIds.indexOf(number) > -1) {
            return this.randomNumber(existingIds);
        } else {
            return number;
        }
    }

    private setupNotificationListener() {
        cordova.plugins.notification.local.on('click', function(notification) {
            this.zone.run(() => {
                if(notification.data.messageId) {
                    this.clicked.next(notification.data.messageId);
                }
            });
        }, this);
    }
}