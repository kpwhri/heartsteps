import { Component } from "@angular/core";
import { ViewController } from "ionic-angular";
import { ActivityTypeService, ActivityType } from "./activity-type.service";

@Component({
    templateUrl: './activity-type-modal.component.html'
})
export class ActivityTypeModalComponent {

    public activityTypes: Array<ActivityType> = [];

    constructor(
        private viewCtrl: ViewController,
        private activityTypeService: ActivityTypeService
    ) {
        this.activityTypeService.load();
        this.activityTypeService.activityTypes.subscribe((activityTypes) => {
            this.activityTypes = activityTypes;
        });
    }

    public select(activityType: ActivityType) {
        this.viewCtrl.dismiss(activityType);
    }

    public dismiss() {
        this.viewCtrl.dismiss();
    }

}
