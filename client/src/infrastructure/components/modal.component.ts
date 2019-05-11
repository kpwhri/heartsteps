import { Component } from "@angular/core";
import { PageComponent } from "./page.component";

@Component({
    selector: 'app-modal',
    templateUrl: './modal.component.html'
})
export class ModalComponent extends PageComponent {

    public dismissible:boolean = true;
    public dismissText: string = "Cancel";

}
