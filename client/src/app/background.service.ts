import { Injectable } from "@angular/core";
import { BackgroundProcessService } from "@infrastructure/background-process.service";
import { LocationService } from "@heartsteps/locations/location.service";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { CurrentActivityLogService } from "@heartsteps/current-week/current-activity-log.service";


@Injectable()
export class BackgroundService{

    constructor(
        private backgroundProcess: BackgroundProcessService,
        private locationService: LocationService,
        private messageReceiptService: MessageReceiptService,
        private currentWeekService: CurrentWeekService,
        private currentActivityLogService: CurrentActivityLogService
    ) {}

    init() {

        this.currentWeekService.setUp();
        this.currentActivityLogService.update();

        this.backgroundProcess.registerTask(() => {
            return this.locationService.saveLocation();
        });
        this.backgroundProcess.registerTask(() => {
            return this.messageReceiptService.sync();
        })
    }
}