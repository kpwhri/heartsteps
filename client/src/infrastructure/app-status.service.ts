import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

export const APP_STATUS = {
    AUTHENTICATED: "AUTHENTICATED",
    NOT_AUTHENTICATED: "NOT_AUTHENTICATED",
    UNKNWON: "UNKNOWN"
} as const;

@Injectable()
export class AppStatusService {
    
    constructor(private heartstepsServer: HeartstepsServer) {
        console.log("src", "infrastructure", "app-status.service.ts", "AppStatusService", "constructor()");
    }

    public getStatus(): Promise<string> {
        return this.heartstepsServer.get('app-status')
            .then((result) => {
                if (result == 'authenticated') {
                    return Promise.resolve(APP_STATUS.AUTHENTICATED);
                } else if (result == 'not authenticated') {
                    return Promise.resolve(APP_STATUS.NOT_AUTHENTICATED);
                }
            })
            .catch((error) => {
                return Promise.reject("Error occured during app status check:" + error);
            });
    }
}