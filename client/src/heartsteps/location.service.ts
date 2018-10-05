import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { LocationService as LocationInfrastructureService } from '@infrastructure/location.service';
import { Geoposition } from "@ionic-native/geolocation";


@Injectable()
export class LocationService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private location: LocationInfrastructureService
    ) {}

    saveLocation(): Promise<boolean> {
        return this.location.getLocation()
        .then((location: Geoposition) => {
            return this.heartstepsServer.post('locations', {
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
                source: 'heartsteps-client'
            });
        })
        .then(() => {
            return Promise.resolve(true);
        });
    }
}