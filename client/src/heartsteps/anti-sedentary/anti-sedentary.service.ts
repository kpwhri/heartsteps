import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";



@Injectable()
export class AntiSedentaryService {

    constructor(
        private heartstepsServer: HeartstepsServer
    ) {}

    public sendTestMessage():Promise<boolean> {
        return this.heartstepsServer.post('anti-sedentary', {})
        .then(() => {
            return true;
        });
    }

}
