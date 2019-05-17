import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { FormGroup, FormControl, Validators } from '@angular/forms';

declare var google;

@Component({
    selector: 'place-edit',
    templateUrl: 'place-edit.html'
})
export class PlaceEdit implements OnInit {

    public pageTitle:string;
    public error: string;
    public showMap: boolean;

    private address:string;

    private latitude:Number;
    private longitude:Number;

    private mapLat:Number;
    private mapLng:Number;

    @ViewChild('map') mapElement: ElementRef;
    private map:any;
    private mapMarker:any;

    private geocoder:any

    private geocoderTimeout:any
    private autocompletionService:any
    public addressPredictions:Array<any>

    private updateView:boolean

    public form: FormGroup;

    constructor(
        params:NavParams,
        private viewCtrl:ViewController
    ) {
        const location = params.get('location')
        if(location) {
            this.address = location.address
            this.latitude = location.latitude
            this.longitude = location.longitude
            this.updateView = true
        } else {
            this.updateView = false
        }

        if(this.updateView) {
            this.pageTitle = 'Edit location'
        } else {
            this.pageTitle = 'Create location'
        }

        this.form = new FormGroup({
            'address': new FormControl(this.address, Validators.required)
        });
        this.form.valueChanges.subscribe((values) => {
            this.showPredictions(values['address']);
        })

        this.autocompletionService = new google.maps.places.AutocompleteService()
        this.geocoder = new google.maps.Geocoder()
    }

    public ngOnInit() {
        this.loadMap()
        if(this.latitude && this.longitude) {
            this.placeMapPin(this.latitude, this.longitude)
        }
    }

    dismiss() {
        this.viewCtrl.dismiss()
    }

    update() {
        if(this.latitude && this.longitude) {
            this.viewCtrl.dismiss({
                address: this.address,
                latitude: this.latitude,
                longitude: this.longitude
            });
        } else {
            this.error = 'No address selected';
        }
    }

    delete() {
        this.viewCtrl.dismiss(false)
    }

    showPredictions(address) {
        this.error = undefined;
        this.latitude = undefined;
        this.longitude = undefined;
        this.hideMap();

        if(this.geocoderTimeout) {
            clearTimeout(this.geocoderTimeout)
        }

        this.geocoderTimeout = setTimeout(() => {
            this.geocoderTimeout = false
            this.getAddressPredicitions(address)
        }, 250)
    }

    getAddressPredicitions(address) {
        if(!address || address.length < 4) {
            this.addressPredictions = []
            return;
        }

        this.autocompletionService.getPlacePredictions({
            input: address
        }, (places, status) => {
            if(status != google.maps.places.PlacesServiceStatus.OK) {
                this.addressPredictions = []
            } else {
                if(places.length === 1) {
                    this.getLatLng(places[0].description)
                } else {
                    this.addressPredictions = places
                }
            }
        })
    }

    setAddress(address) {
        this.address = address;
        this.form.patchValue({'address':address});
        this.addressPredictions = undefined;
        this.showMap = true;
        this.getLatLng(address);
    }

    getLatLng(address) {
        this.geocoder.geocode({
            address: address
        }, (results, status) => {
            if(status === 'OK') {
                let result = results[0];
                this.updateLatLng(
                    result.geometry.location.lat(),
                    result.geometry.location.lng()
                )
            }
            
        })
    }

    private updateLatLng(lat, lng) {
        this.latitude = lat;
        this.longitude = lng;
        this.placeMapPin(lat, lng);
    }

    private getMap() {
        if(this.map) {
            return Promise.resolve(this.map)
        } else {
            return this.loadMap().then(() => {
                this.map
            })
        }
    }

    private hideMap() {
        this.showMap = false;
    }

    private loadMap() {
        this.showMap = true;
        return this.getMapLocation()
        .then((latLng) => {
            let mapOptions = {
                center: latLng,
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
            this.map = new google.maps.Map(this.mapElement.nativeElement, mapOptions)
        })
        .catch(() => {
            console.log('didnt show map');
        });
    }

    private placeMapPin(latitude, longitude) {
        if(!latitude || !longitude) {
            return
        }
        this.getMap().then(() => {
            if(this.mapMarker) {
                this.mapMarker.setMap(null)
            }
    
            let latLng = new google.maps.LatLng(latitude, longitude)
            this.map.setCenter(latLng)
            this.mapMarker = new google.maps.Marker({
                position: latLng,
                map: this.map
            });
        })
    }

    private getMapLocation():Promise<any> {
        if(this.latitude && this.longitude) {
            return Promise.resolve(new google.maps.LatLng(
                this.latitude,
                this.longitude
            ));
        } else {
            return Promise.reject('No latitude and longitude available');
        }
    }
}
