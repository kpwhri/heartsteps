import * as moment from 'moment';
import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";



@Component({
    templateUrl: './fitbit-clock-face-pin.page.html'
})
export class FitbitClockFacePinPage implements OnInit {

    public notificationsEnabled:boolean;
    public pin: string;
    public stepCounts: Array<any>;

    public form: FormGroup;

    constructor(
        private heartstepsServer:HeartstepsServer,
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController,
        private router: Router
    ) {}

    ngOnInit() {
        this.form = new FormGroup({
            'pin': new FormControl('', Validators.required)
        });
        this.updatePin()
        .then(() => {
            if(this.pin) {
                this.getLastStepCounts();
            }
        });
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

    public submitForm() {
        if(this.form.valid) {
            this.loadingService.show('Pairing Fitbit Clock Face')
            this.heartstepsServer.post('fitbit-clock-face/pair', {
                'pin': this.form.get('pin').value
            })
            .then(() => {
                this.alertDialog.show('Successfully paired!')
                .then(() => {
                    this.updatePin()
                });
            })
            .catch(() => {
                this.alertDialog.show('Error pairing');
            })
            .then(() => {
                this.loadingService.dismiss()
            });
        }
    }

    public updatePin(): Promise<void> {
        this.loadingService.show('Updating pin');
        return this.heartstepsServer.get('fitbit-clock-face/pair')
        .then((data) => {
            this.pin = data.pin;
        })
        .catch(() => {
            this.pin = undefined;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public getLastStepCounts(): Promise<void> {
        this.loadingService.show('Getting recent step count')
        return this.heartstepsServer.get('fitbit-clock-face/step-counts')
        .then((data) => {
            if (data.step_counts && Array.isArray(data.step_counts)) {
                this.stepCounts = data.step_counts.map((step_count) => { 
                    return {
                        'start': moment(step_count.start).fromNow(),
                        'end': moment(step_count.end).fromNow(),
                        'steps': step_count.steps
                    }
                })
            } else {
                this.stepCounts = undefined;
            }
        })
        .catch(() => {
            this.alertDialog.show('Error step counts');
        })
        .then(() => {
            this.loadingService.dismiss()
        })
    }

    public deletePin(): Promise<void> {
        this.loadingService.show("Deleting pin");
        return this.heartstepsServer.delete('fitbit-clock-face/pair')
        .then(() => {
            this.pin = undefined;
            this.stepCounts = undefined;
            this.alertDialog.show('Deleted');
        })
        .catch(() => {
            this.alertDialog.show('Error deleting pin');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
