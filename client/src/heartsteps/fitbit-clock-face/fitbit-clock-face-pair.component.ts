import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { LoadingService } from "@infrastructure/loading.service";
import { FitbitClockFaceService } from "./fitbit-clock-face.service";


@Component({
    selector: 'heartsteps-fitbit-clock-face-pair',
    templateUrl: './fitbit-clock-face-pair.component.html'
})
export class FitbitClockFacePairComponent implements OnInit {

    @Output() paired: EventEmitter<void> = new EventEmitter();

    public form: FormGroup;

    constructor(
        private fitbitClockFaceService: FitbitClockFaceService,
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController
    ) {}

    ngOnInit() {
        this.form = new FormGroup({
            'pin': new FormControl('', Validators.required)
        });
    }

    public submitForm() {
        if(this.form.valid) {
            this.loadingService.show('Pairing Fitbit Clock Face');
            const pin = this.form.get('pin').value;
            this.fitbitClockFaceService.pairWithPin(pin)
            .then(() => {
                this.alertDialog.show('Successfully paired!')
                .then(() => {
                    this.paired.emit();
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

}