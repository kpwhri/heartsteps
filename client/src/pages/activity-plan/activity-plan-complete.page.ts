import { Component } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './activity-plan-complete.page.html'
})
export class ActivityPlanCompletePage {

    public plan:ActivityPlan;
    public form:FormGroup;

    constructor(
        private activityPlanService: ActivityPlanService,
        private activityLogService: ActivityLogService,
        private loadingService: LoadingService,
        activatedRoute: ActivatedRoute,
        private router: Router
    ){
        this.plan = activatedRoute.snapshot.data['activityPlan'];
        this.form = new FormGroup({
            activityPlan: new FormControl(this.plan, Validators.required),
            effort: new FormControl(),
            enjoyed: new FormControl()
        });
    }

    public complete() {
        this.loadingService.show('Completing activity plan');
        const activityPlan:ActivityPlan = this.form.value.activityPlan;
        this.activityPlanService.complete(activityPlan)
        .then((activityPlan) => {
            return this.activityLogService.getLog(activityPlan.activityLogId)
        })
        .then((activityLog: ActivityLog) => {
            activityLog.enjoyed = this.form.value.enjoyed;
            activityLog.effort = this.form.value.effort;
            this.activityLogService.save(activityLog);
        })
        .then(() => {
            this.dismiss();
        })
        .catch((errors) => {
            console.log(errors);
        })
        .then(() => {
            this.loadingService.dismiss()
        });
    }

    public editPlan() {
        this.router.navigate([{outlets: {
            modal: ['plans', this.plan.id].join('/')
        }}]);
    }

    public dismiss() {
        this.router.navigate([{outlets:{modal:null}}]);
    }

}
