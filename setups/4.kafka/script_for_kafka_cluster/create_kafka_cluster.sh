#!/bin/bash
echo "########################################################################################################################"
echo "############################                                             ###############################################"
echo "############################                                            ################################################"
echo "##############################################################         #################################################"
echo "#############################################################         ##################################################"
echo "############################################################         ###################################################"
echo "###########################################################         ####################################################"
echo "##########################################################         #####################################################"
echo "#########################################################         ######################################################"
echo "########################################################         #######################################################"
echo "#######################################################         ########################################################"
echo "######################################################         #########################################################"
echo "#####################################################         ##########################################################"
echo "####################################################         ###########################################################"
echo "###################################################         ############################################################"
echo "##################################################         #############################################################"
echo "#################################################         ##############################################################"
echo "################################################         ###############################################################"
echo "###############################################         ################################################################"
echo "##############################################         #################################################################"
echo "#############################################         ##################################################################"
echo "############################################         ###################################################################"
echo "########################################################################################################################"

source ./exports.sh
# kafka_nodes=${no_kafka_nodes}
# echo $kafka_nodes
for (( i=1; i<=${no_kafka_nodes}; i++ ))
do
    echo "Create kafka-broker-$i node in the cluster"

    mod=$((i % 3))

    if [ $mod == "0" ] 
    then
        region_zone=${region_zone_a} 
    elif [ $mod == "1" ] 
    then
        region_zone=${region_zone_b}
    else 
        region_zone=${region_zone_c}
    fi

    gcloud beta compute instances create kafka-broker-$i \
        --source-machine-image kafka-machine-image  \
        --zone $region_zone \
        --machine-type ${kafka_machine_type} \
        --subnet ${vpc_subnet} \
        --tags kafka \
        --labels=application=kafka \
        --no-address    

    sleep 20

    private_ip_address=$(gcloud compute instances describe kafka-broker-$i --zone=$region_zone | grep networkIP:)
    private_ip_address=$(cut -d ":" -f2- <<< $private_ip_address)
    private_ip_address=$(echo $private_ip_address | xargs)

    cp server_base.properties server.properties

    sed -i "s%<<project-id>>%$project_id%g" "server.properties"
    sed -i "s%<<private_ip_address>>%$private_ip_address%g" "server.properties"
    sed -i "s%<<id>>%$i%g" "server.properties"

    sleep 10

    gcloud compute scp ./server.properties kafka-broker-$i:/tmp --zone=$region_zone --tunnel-through-iap --project=$project_id
    gcloud compute ssh kafka-broker-$i \
    --tunnel-through-iap \
    --zone=$region_zone \
    --command 'sudo mv /tmp/server.properties /opt/kafka/config/'

    #gcloud compute scp ./server.properties kafka-broker-4:/tmp --zone=us-east4-b --tunnel-through-iap --project=d11-logging
    # gcloud compute ssh kafka-broker-4 \
    # --tunnel-through-iap \
    # --zone=us-east4-b \
    # --command 'sudo mv /tmp/server.properties /opt/kafka/config/'

    gcloud compute ssh kafka-broker-$i \
    --tunnel-through-iap \
    --zone=$region_zone \
    --command 'sudo rm -rf /data/kafka/logs/ && sudo systemctl enable kafka.service && sudo systemctl start kafka.service'

    rm -rf server.properties

done
