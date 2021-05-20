import { NgModule } from "@angular/core";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { GenericMessagesService } from "./generic-messages.service";



@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        GenericMessagesService
    ]
})
export class GenericMessagesModule {}