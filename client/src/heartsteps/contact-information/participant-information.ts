import { Component, Output, EventEmitter } from '@angular/core';
import { ContactInformationService } from '@heartsteps/contact-information/contact-information.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';

@Component({
    selector: 'heartsteps-participant-information',
    templateUrl: 'participant-information.html'
})
export class ParticipantInformation {

    public contactInformationForm: FormGroup;
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private contactInformationService:ContactInformationService,
        private loadingService:LoadingService
    ) {
        this.setupForm();
        this.contactInformationService.get()
        .then((contactInformation:any) => {
            this.setupForm(
                contactInformation.name,
                contactInformation.email,
                contactInformation.phone
            )
        })
        .catch(() => {
            console.log('No previous contact information');
        });
    }

    private setupForm(name?:string, email?:string, phone?:string):void {
        this.contactInformationForm = new FormGroup({
            name: new FormControl(name, Validators.required),
            email: new FormControl(email, [Validators.required, Validators.email]),
            phone: new FormControl(phone, Validators.required)
        });
    }

    save() {
        if(this.contactInformationForm.valid) {
            this.loadingService.show('Saving contact information')
            this.contactInformationService.save(this.contactInformationForm.value)
            .then(() => {
                this.saved.emit(true);
            })
            .then(() => {
                this.loadingService.dismiss()
            })
        }
    }

}
