import { Component } from "@angular/core";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { LoadingService } from "@infrastructure/loading.service";
import { DateFactory } from "@infrastructure/date.factory";


@Component({
    templateUrl: './activity-log-create.page.html'
})
export class ActivityLogCreatePage {

    public activityLog: ActivityLog;
    public error: string;

    constructor(
        private activityLogService: ActivityLogService,
        private router: Router,
        private activatedRoute: ActivatedRoute,
        private loadingService: LoadingService,
        private dateFactory: DateFactory
    ) {
        this.activityLog = new ActivityLog();

        const dateStr = this.activatedRoute.snapshot.queryParamMap.get('date');
        if (dateStr) {
            this.activityLog.start = this.dateFactory.parseDate(dateStr);
        } else {
            this.activityLog.start = new Date();
        }

    }

    public create(activityLog: ActivityLog) {
        this.loadingService.show('Creating activity log');
        this.activityLogService.save(activityLog)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public dismiss() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }


}
