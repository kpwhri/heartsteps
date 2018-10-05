import { Injectable } from "@angular/core";
import { BackgroundProcessService } from "@infrastructure/background-process.service";
import { LocationService } from "@heartsteps/location.service";


@Injectable()
export class BackgroundService{

    constructor(
        private backgroundProcess: BackgroundProcessService,
        private locationService: LocationService
    ) {
        backgroundProcess.registerTask(() => {
            return this.locationService.saveLocation();
        });
    }
}