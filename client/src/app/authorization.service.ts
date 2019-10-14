import { Injectable } from "@angular/core";
import { AuthorizationService as AuthorizationInfrastructure } from '@infrastructure/authorization.service'
import { EnrollmentController } from "@heartsteps/enrollment/enrollment.controller";
import { ParticipantService } from "@heartsteps/participants/participant.service";


@Injectable()
export class AuthorizationService {

    constructor(
        private authorizationInfrastructure: AuthorizationInfrastructure,
        private participantService: ParticipantService,
        private enrollmentController: EnrollmentController
    ) {}

    public setup(): Promise<void> {
        this.authorizationInfrastructure.onRetryAuthorization(() => {
            return this.enrollmentController.enroll("Please re-authenticate", false)
            .then(() => {
                return this.authorizationInfrastructure.isAuthorized();
            })
            .catch(() => {
                return this.participantService.remove()
                .then(() => {
                    return Promise.reject(false);
                });
            });
        });
        return Promise.resolve(undefined);
    }

    public reset() {
        this.authorizationInfrastructure.removeRetryAuthorization();
    }
}

