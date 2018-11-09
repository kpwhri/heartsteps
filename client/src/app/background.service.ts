import { Injectable } from "@angular/core";
import { BackgroundProcessService } from "@infrastructure/background-process.service";
import { LocationService } from "@heartsteps/locations/location.service";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";


@Injectable()
export class BackgroundService{

    constructor(
        private backgroundProcess: BackgroundProcessService,
        private locationService: LocationService,
        private messageReceiptService: MessageReceiptService
    ) {}

    init() {
        this.backgroundProcess.registerTask(() => {
            return this.locationService.saveLocation();
        });
        this.backgroundProcess.registerTask(() => {
            return this.messageReceiptService.sync();
        })
    }
}