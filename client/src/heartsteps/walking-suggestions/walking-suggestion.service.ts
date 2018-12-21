import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { LocationService } from "@infrastructure/location.service";


@Injectable()
export class WalkingSuggestionService {

    constructor(
        private locationService: LocationService,
        private heartstepsServer: HeartstepsServer,
    ){}

    sendDecisionContext(decisionId:string) {
        this.locationService.getLocation().then((position:any) => {
            this.heartstepsServer.post('/walking-suggestions/'+decisionId, {
                location: {
                    latitude: position.latitude,
                    longitude: position.longitude
                }
            });
        });
    }
}
