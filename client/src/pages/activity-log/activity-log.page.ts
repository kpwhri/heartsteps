import { Component } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { LoadingService } from "@infrastructure/loading.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";


@Component({
    templateUrl: './activity-log.page.html'
})
export class ActivityLogPage {

    public activityLog:ActivityLog;
    public error: string;

    constructor(
        private activatedRoute: ActivatedRoute,
        private loadingService: LoadingService,
        private activityLogService: ActivityLogService,
        private router: Router
    ) {
        this.activityLog = this.activatedRoute.snapshot.data['activityLog'];
    }

    public update(activityLog: ActivityLog) {
        console.log(activityLog);
        this.loadingService.show('Updaing activity log');
        activityLog.id = this.activityLog.id;
        this.activityLogService.save(activityLog)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public delete() {
        this.loadingService.show('Deleting activity log');
        this.activityLogService.delete(this.activityLog)
        .then(() => {
            this.dismiss()
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loadingService.dismiss()
        });
    }

    dismiss() {
        this.router.navigate([{outlets: {
            modal: null
        }}]);
    }
}
