import { Component, ViewChild, ElementRef } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';

declare var google;

@Component({
    selector: 'location-edit',
    templateUrl: 'location-edit.html'
})
export class LocationEdit {

    private address:String
    private type:String

    private lat:Number
    private lng:Number

    @ViewChild('map') mapElement: ElementRef
    private map:any

    private geocoder:any
    private geocoderTimeout:any

    private currentLocation:any

    constructor(
        params:NavParams,
        private viewCtrl:ViewController
    ) {
        const location = params.get('location')
        this.address = location.address
        this.type = location.type
        this.lat = location.lat
        this.lng = location.lng

        this.currentLocation = params.get('currentLocation')

        this.geocoder = new google.maps.Geocoder()
    }

    ionViewDidLoad() {
        this.loadMap()
        this.placeMapPin()
    }

    update() {
        this.viewCtrl.dismiss({
            address: this.address,
            type: this.type
        })
    }

    updateLatLng() {
        if(this.geocoderTimeout) {
            clearTimeout(this.geocoderTimeout)
        }

        this.geocoderTimeout = setTimeout(() => {
            this.geocoderTimeout = false
            this.getLatLng()
        }, 2000)
    }

    getLatLng() {
        this.geocoder.geocode({
            address: this.address
        }, (results, status) => {
            if(status === 'OK') {
                let result = results[0];
                this.lat = result.geometry.location.lat()
                this.lng = result.geometry.location.lng()
                this.placeMapPin()
            }
            
        })
    }

    loadMap() {
        let latLng = new google.maps.LatLng(this.currentLocation.lat, this.currentLocation.lng);
        if(this.lat && this.lng) {
            latLng = new google.maps.LatLng(this.lat, this.lng);
        }
 
        let mapOptions = {
          center: latLng,
          zoom: 10,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }
     
        this.map = new google.maps.Map(this.mapElement.nativeElement, mapOptions);
    }

    placeMapPin() {
        if(!this.lat || !this.lng) {
            return
        }
        let latLng = new google.maps.LatLng(this.lat, this.lng)
        this.map.setCenter(latLng)
        new google.maps.Marker({
            position: latLng,
            map: this.map
        });
    }
}
