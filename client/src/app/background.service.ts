import { Injectable } from "@angular/core";
import { LocationService } from "@heartsteps/locations/location.service";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";


@Injectable()
export class BackgroundService{

    constructor(
        private locationService: LocationService,
        private messageReceiptService: MessageReceiptService,
    ) {}

    init() {
        
    }
}