#!/usr/bin/perl

use VMware::VIRuntime;
use VMware::VILib;
use Data::Dumper qw(Dumper);
use AppUtil::HostUtil;
use AppUtil::VMUtil;
use POSIX qw/strftime/;

## This was made with the intent to scan all VCENTER and return a list of all VMs Guest and some predetermined infos.
# Properties I care about on this are:
# - VM name
# - VM stat
# - VM GuestID (O.S.)
# - VM number of vCPUs
# - VM total ram mem
# - VM num of vdks
# - VM total size of all VDKs
# - VM immediate parent Resource Pool name
#
# You can extend:
# - https://www.vmware.com/support/developer/viperltoolkit/
# - https://www.vmware.com/support/developer/vc-sdk/visdk25pubs/ReferenceGuide/left-pane.html
#

my $username            = "myvcenteruser";
my $password            = "mypassword";
my $vcenterHost         = "myvcenter.mydomain.com";


$host_address = "https://" . $vcenterHost . "/sdk/webService";
eval {
	Util::connect($host_address, $username, $password);
};
if ($@) {
	die "Could not connect to $host_address using $username username\n";
}

my $result  =  Vim::find_entity_views ( view_type => 'VirtualMachine', properties => [ 'name','summary','config.hardware.device', 'resourcePool' ] );
my $rgroups =  Vim::find_entity_views ( view_type => 'ResourcePool'  , properties => [ 'name', 'config.entity', 'parent' ] );

##print $result;
##print Dumper($result);

print "NAME,STATE,GUESTID,CPUS,MEMSIZE_MB,NUMVDKS,TOTALVDKSSIZE_MB,RPOOL"."\n";

foreach my $vm(@$result) {
	my @devicesArr = $vm->get_property('config.hardware.device');
	my $totalDiskSize = 0;
	my $rpool = $vm->{resourcePool}->{value};

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
				$rpool = $prev->{name};
			}
			break;
		}
	}

	$totalDiskSize = $totalDiskSize/1024;
	print $vm->name.",".$vm->summary->runtime->powerState->val.",".$vm->summary->config->guestId.",".$vm->summary->config->numCpu.",".$vm->summary->config->memorySizeMB.",".$vm->summary->config->numVirtualDisks.",".$totalDiskSize.",".$rpool."\n";

}

Util::disconnect();
