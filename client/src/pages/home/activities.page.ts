import { Component, OnInit } from "@angular/core";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";

@Component({
    templateUrl: './activities.page.html'
})
export class ActivitiesPage implements OnInit {

    public days: Array<Date>

    constructor(
        private cachedActivityLogService: CachedActivityLogService
    ){
        this.cachedActivityLogService.getCachedDates()
        .then((cachedDates) => {
            this.days = cachedDates.reverse();
            this.cachedActivityLogService.update();
        });
    }

    ngOnInit() {

    }
    
}
