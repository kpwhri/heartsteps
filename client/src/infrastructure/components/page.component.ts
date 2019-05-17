import { Component, Input, Output, EventEmitter } from "@angular/core";

@Component({
    selector: 'app-page',
    templateUrl: './page.component.html'
})
export class PageComponent {

    @Input('title') title: string;
    @Output('onDismiss') onDismiss: EventEmitter<boolean> = new EventEmitter();

    public dismissible: boolean = false;
    public dismissText;

    constructor() {}

    @Input('dismiss')
    set setDismiss(value: string) {
        if (value) {
            this.dismissible = true;
            this.dismissText = value;
        } else {
            this.dismissible = false;
            this.dismissText = undefined;
        }
    }

    public dismiss() {
        this.onDismiss.emit();
    }

}
