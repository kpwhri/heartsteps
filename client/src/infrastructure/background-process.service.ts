import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";

@Injectable()
export class BackgroundProcessService{

    callbacks: Array<Function> = [];

    constructor(
        platform:Platform
    ){
        platform.ready()
        .then(() => {
            this.setupBackgroundFetch();
        })
    }

    setupBackgroundFetch() {
        const backgroundFetch = (<any>window).BackgroundFetch;
        const fetchCalllback = () => {
            this.runTasks()
            .then(() => {
                backgroundFetch.finish();
            });
        }
        const failureCallback = function(error) {
            console.log("Background fetch failed", error)
        }
        backgroundFetch.configure(fetchCalllback, failureCallback, {
            minimumFetchInterval: 30
        });
    }

    runTasks(): Promise<boolean> {
        if(this.callbacks && this.callbacks.length) {
            const promises = this.callCallbacks();
            return Promise.all(promises)
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(true);
            });
        } else {
            return Promise.resolve(true);
        }
    }

    callCallbacks(): Array<Promise<any>> {
        const promises: Array<Promise<any>> = [];
        this.callbacks.forEach((callback: Function) => {
            const result = callback();
            promises.push(result);
        })
        return promises;
    }

    registerTask(callback: Function) {
        this.callbacks.push(callback);
        
        // return unregister function
        return function() {
            this.callbacks.forEach( (element, index) => {
                if (element === callback) {
                    this.callbacks.splice(index, 1);
                }
            });
        };
    }
}
