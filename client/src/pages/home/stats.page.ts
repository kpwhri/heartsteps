import { Component, OnInit } from "@angular/core";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";

@Component({
    templateUrl: './stats.page.html'
})
export class StatsPage implements OnInit {

    public days: Array<Date>

    constructor(
        private cachedActivityLogService: CachedActivityLogService
    ){
        this.days = this.cachedActivityLogService.getCachedDates().reverse();
        this.cachedActivityLogService.update();
    }

    ngOnInit() {

    }
    
}
