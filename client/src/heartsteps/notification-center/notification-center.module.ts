import { NgModule } from "@angular/core";

import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { NotificationCenterService } from "./notification-center.service";

// TODO: learn about NgModule, diff b/w imports, declarations, providers
@NgModule({
    imports: [InfrastructureModule],
    providers: [NotificationCenterService],
})
export class NotificationCenterModule {}
