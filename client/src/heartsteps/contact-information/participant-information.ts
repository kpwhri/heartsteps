import { Component, Output, EventEmitter } from '@angular/core';
import { ContactInformationService } from '@heartsteps/contact-information/contact-information.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'heartsteps-participant-information',
    templateUrl: 'participant-information.html'
})
export class ParticipantInformation {

    public contactInformationForm: any
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private contactInformationService:ContactInformationService,
        private loadingService:LoadingService,
        private formBuilder:FormBuilder
    ) {
        this.contactInformationService.get()
        .then((contactInformation:any) => {
            return contactInformation
        })
        .catch(() => {
            return {
                name: '',
                email: '',
                phone: ''
            }
        })
        .then((contactInformation) => {
            this.contactInformationForm = this.formBuilder.group({
                name: [contactInformation.name, Validators.required],
                email: [contactInformation.email, [Validators.email, Validators.required]],
                phone: [contactInformation.phone, Validators.required]
            })
        })
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
