import { Component } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { LoadingService } from "@infrastructure/loading.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { FormGroup, FormControl } from "@angular/forms";

@Component({
    templateUrl: './activity-plan.page.html'
})
export class ActivityPlanPage {

    public activityPlan: ActivityPlan;
    public planForm: FormGroup;
    public disabled: boolean;

    constructor(
        private activityPlanService: ActivityPlanService,
        private loadingService: LoadingService,
        private alertDialogController: AlertDialogController,
        activatedRoute: ActivatedRoute,
        private router: Router
    ) {
        this.activityPlan = activatedRoute.snapshot.data['activityPlan'];
        this.planForm = new FormGroup({
            activityPlan: new FormControl(this.activityPlan)
        });
        if(this.activityPlan.isComplete()) {
            this.disabled = true;
        }
    }

    public update() {
        this.loadingService.show('Updating activity plan');
        const activityPlan: ActivityPlan = this.planForm.value.activityPlan;
        this.activityPlanService.save(activityPlan)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            this.alertDialogController.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public goToComplete() {
        this.router.navigate([{outlets: {
            modal: ['plans', this.activityPlan.id, 'complete'].join('/')
        }}]);
    }

    public goToActivityLog() {
        this.router.navigate([{outlets: {
            modal: ['activities/logs', this.activityPlan.activityLogId].join('/')
        }}]);
    }

    public delete() {
        this.loadingService.show('Deleting activity plan');
        this.activityPlanService.delete(this.activityPlan)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            this.alertDialogController.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public uncomplete() {
        this.loadingService.show('Making activity plan incomplete')
        this.activityPlanService.uncomplete(this.activityPlan)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            this.alertDialogController.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public dismiss() {
        this.router.navigate([{outlets:{modal:null}}]);
    }

}
