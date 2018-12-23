import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { LocationService as LocationInfrastructureService } from '@infrastructure/location.service';


@Injectable()
export class LocationService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private location: LocationInfrastructureService
    ) {}

    saveLocation(): Promise<boolean> {
        return this.location.getLocation()
        .then((location: any) => {
            return this.heartstepsServer.post('locations', {
                latitude: location.latitude,
                longitude: location.longitude,
                source: 'heartsteps-client'
            });
        })
        .then(() => {
            return Promise.resolve(true);
        });
    }
}