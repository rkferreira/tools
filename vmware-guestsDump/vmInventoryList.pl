#!/usr/bin/perl

###
## This is V2 of same script.
# You dont necessary need all of this, we needed, so it was done.
#

$|++;
use VMware::VIRuntime;
use VMware::VILib;
use Data::Dumper qw(Dumper);
use AppUtil::HostUtil;
use AppUtil::VMUtil;
use POSIX qw/strftime/;


my $username            = "myvcenteruser";
my $password            = "mypass";
my $vcenterHost         = "myvcenter.host";

my $guestCompany	= "fixed-CompanyValue";
my $guestModelName	= "Virtual Machine";
my $guestManufacter	= "VMWARE";
my $guestDomain		= "fixed-AdministrationDomain";

my $LABEL		= "Item Name,Domain,Status,Operating System,vCPU Quantity,Memory (MB),VMDK Quantity,Allocated Disk (MB),Team,Company,Model Name,Manufacturer,Supplier,Location,Asset Tag";


#Dictionaries for translations
#
my %t_location = ( NYC  => "NEWYORK", SAO => "SAOPAULO", MIA  => "MIAMI" );
my %t_status   = ( poweredOn => "Production", poweredOff => "Powered Off" );
my %t_guestid  = ( linuxGuest => "Linux", windowsGuest => "Windows" );
my %t_team     = ( 'MyLocalTeam1' => "Team1", 'MyLocalTeam2' => "Team2" );


sub translate {
	my $dict1       = shift;
	my $value       = shift;
	my %dict2       = %$dict1;

	if (!length($value)) {
		$value = "NONE";
	}
	if ($dict2{$value}) {
		return $dict2{$value};
	} else {
		return $value;
	}
}


sub main {
	$host_address = "https://" . $vcenterHost . "/sdk/webService";
	eval {
		Util::connect($host_address, $username, $password);
	};
	if ($@) {
		die "Could not connect to $host_address using $username username\n";
	}

	my $result  =  Vim::find_entity_views ( view_type => 'VirtualMachine', properties => [ 'name','summary','config.hardware.device','resourcePool','guest' ] );
	my $rgroups =  Vim::find_entity_views ( view_type => 'ResourcePool'  , properties => [ 'name','config.entity','parent' ] );

	print $LABEL."\n";

	foreach my $vm(@$result) {
		my @devicesArr 		= $vm->get_property('config.hardware.device');
		my $totalDiskSize 	= 0;
		my $rpool 		= $vm->{resourcePool}->{value};
		my $datacenter		= undef;

		foreach my $o ($devicesArr[0]) {
			foreach my $p (@$o){
				while( my ($k, $v) = each %$p ) {
					if ( $k eq 'capacityInKB' ) {
						$totalDiskSize = $totalDiskSize + $v;
					}
				 }
			}
		}
		foreach my $r (@$rgroups) {
			my $temp = $r->{'config.entity'}->{value};
			if ($rpool eq $temp) {
				$rpool = $r->{name};
				if ( $r->{'parent'}->{'value'} =~ /resgroup/ ) {
					my $f = Vim::get_view(mo_ref => $r->{'parent'});
					my $prev = $r;

					while ( $f->{'parent'}->{'value'} =~ /resgroup/  ) {
						$prev = $f;
						$f = Vim::get_view(mo_ref => $f->{'parent'});
					}
					$rpool   = $prev->{name};
					for ($a=0;  $a<3; $a=$a+1) {
						$f = Vim::get_view(mo_ref => $f->{'parent'});
					}
					$datacenter = $f->{name};
				}
				break;
			}
		}

		$totalDiskSize = $totalDiskSize/1024;
		$temp2 = $totalDiskSize;
		$totalDiskSize = sprintf("%.0f", $temp2);
		print $vm->name.",".$guestDomain.",".translate(\%t_status, $vm->summary->runtime->powerState->val).",".translate(\%t_guestid, $vm->guest->guestFamily).",".$vm->summary->config->numCpu.",".$vm->summary->config->memorySizeMB.",".$vm->summary->config->numVirtualDisks.",".$totalDiskSize.",".translate(\%t_team, $rpool).",".$guestCompany.",".$guestModelName.",".$guestManufacter.",".$guestManufacter.",".translate(\%t_location, $datacenter).",".$vm->summary->config->uuid."\n";
	}

	Util::disconnect();
}

main();
