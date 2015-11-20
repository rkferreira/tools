#!/usr/bin/perl

# *
# # *  Copyright 2014 by Rodrigo Kellermann Ferreira <rkferreira@gmail.com>
# # *        <http://www.gnu.org/licenses/>.

use VMware::VIRuntime;
use VMware::VILib;
use Data::Dumper qw(Dumper);
use AppUtil::HostUtil;
use AppUtil::VMUtil;
use POSIX qw/strftime/;


my $username		= "vcenterUserName";
my $password		= "vcenterPassword";
my $vcenterHost		= "vcenter.mydomain.com";
my $srcCluster		= "SRC_CLUSTER";
my $dstCluster		= "DST_CLUSTER";
my $dstPool		= "Migrated";


# Global -> Force flush
$|++;
# Log
my $logB = undef ;

sub findSingleCCR {
	( $filter ) = @_;
	
	my $result = Vim::find_entity_view  ( view_type => 'ClusterComputeResource', properties => [ 'name', 'host' ], filter => { 'name' => $filter } );
	return $result;
}

sub findMultHS {
	( $filter ) = @_;

	my $result = Vim::find_entity_views ( view_type => 'HostSystem', begin_entity => $filter, properties => [ 'name', 'runtime' , 'datastore' ] );
	return $result;
}

sub findSingleVM {
	( $filter_entity, $filter ) = @_;

	my $result =  Vim::find_entity_view ( view_type => 'VirtualMachine', begin_entity => $filter_entity, properties => [ 'name', 'datastore', 'config' ], filter => { 
						'config.guestFullName' => qr/Windows/, } 
			);
	return $result;
}

sub findMultVM {
	( $filter_entity, $filter ) = @_;

	my $result =  Vim::find_entity_views ( view_type => 'VirtualMachine', begin_entity => $filter_entity, properties => [ 'name', 'datastore', 'config' ], filter => { 
						'config.guestFullName' => qr/Windows/, } 
			);
	print $result ;
	return $result;
}

sub getDstHostSystem {
	( $hostView, $maxRand ) = @_;

	my $result	= undef;
	my $irand	= int(rand($maxRand));
	my $aux		= 0;

	foreach my $a (@$hostView) {
		if ($a->runtime->inMaintenanceMode == 0 and $aux==$irand) {
			$result = $a;
		}
		$aux++;
	}	

	return $result;
}

sub getCurDataStore {
	( $datastoreurl ) = @_;
	
	my $result;
	foreach my $a ($datastoreurl) {
		foreach my $b (@$a) {
			$result = $b->name;
		}
	}
	
	return $result;
}

sub main {
	my $mySeed		= time();
	my $runPID		= srand( rand(~0) ^ $mySeed );
	$logB			= "\n $runPID - ";
	my $res			= undef ;
	my $dstClusterView	= undef ;
	my $dstHostView		= undef ;
	my $srcClusterView	= undef ;
	my $tgtVmView		= undef ;
	my $tgtVmViewMult	= undef ;
	my $tgtHostView		= undef ;
	my $curDataStore	= undef ;
	my %DatastoreInfo	= undef ;
	my %Pool		= undef ;
	
	print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " - Begin";

	$host_address = "https://" . $vcenterHost . "/sdk/webService";

	eval {
		Util::connect($host_address, $username, $password);
	};
	if ($@) {
		die "Could not connect to $host_address using $username username\n";
	}

	$dstClusterView	= findSingleCCR( $dstCluster );
	$dstHostView	= findMultHS( $dstClusterView );
	$tgtHostView	= getDstHostSystem( $dstHostView , "4" );
	print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Migrating to <" . $tgtHostView->name . "> host.";
	$srcClusterView	= findSingleCCR( $srcCluster );
	$tgtVmView	= findSingleVM( $srcClusterView, "qr/Windows/" );

	if ($tgtVmView) {
		print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Selected VM <" . $tgtVmView->name . "> for migration.";
		$curDataStore	= getCurDataStore($tgtVmView->config->datastoreUrl);
		print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Current Datastore is <" . $curDataStore . ">";
		%DatastoreInfo	= HostUtils::get_datastore( host_view => $tgtHostView , datastore => $curDataStore, disksize => 1024 );
		print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Migrating to <" . $DatastoreInfo{name} . "> datastore.";
		%Pool		= HostUtils::check_pool( poolname =>$dstPool, targethost => $tgtHostView->name  );
		print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Checking if pool <" . $dstPool . "> is present on <" . $tgtVmView->name . ">. Result is: " . $Pool{foundhost} . "\n";
	        $res		= VMUtils::relocate_virtualmachine( vm => $tgtVmView , pool => $Pool{mor}, targethostview => $tgtHostView, datastore => $DatastoreInfo{mor} ); 
		if ($res eq 0) {
			$tgtVmViewMult	= findMultVM( $srcClusterView, "qr/Windows/" );
			my $got = 0;
			foreach my $a (@$tgtVmViewMult) {
				if ($got == 0) {
					if ($a->name eq $tgtVmView->name) {
						next;
					} else {
						$tgtVmView = $a;
						print "\n";
						$curDataStore   = getCurDataStore($tgtVmView->config->datastoreUrl);
				                print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Current Datastore is <" . $curDataStore . ">";
				                %DatastoreInfo  = HostUtils::get_datastore( host_view => $tgtHostView , datastore => $curDataStore, disksize => 1024 );
				                print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Migrating to <" . $DatastoreInfo{name} . "> datastore.";
						$res = VMUtils::relocate_virtualmachine( vm => $tgtVmView , pool => $Pool{mor}, targethostview => $tgtHostView, datastore => $DatastoreInfo{mor} );
						#if ($res eq 1) { #doesnt work
						$got++;
						break;
						#}
							
						
					}
				}
			}
		}
	} else {
		print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " Nothing to do.";

	}
	Util::disconnect();
	print $logB . strftime('%Y-%m-%d_%T_%s',localtime) . " - End\n";
}

main();



#print Dumper($result);
