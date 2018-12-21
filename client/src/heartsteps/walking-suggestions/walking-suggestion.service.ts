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

        this.locationService.getLocation().then((position:Position) => {
            this.heartstepsServer.post('/walking-suggestions/'+decisionId, {
                location: {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                }
            })
        })

    }
}
