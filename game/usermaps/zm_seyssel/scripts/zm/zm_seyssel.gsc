#using scripts\codescripts\struct;

#using scripts\shared\array_shared;
#using scripts\shared\callbacks_shared;
#using scripts\shared\clientfield_shared;
#using scripts\shared\compass;
#using scripts\shared\exploder_shared;
#using scripts\shared\flag_shared;
#using scripts\shared\laststand_shared;
#using scripts\shared\math_shared;
#using scripts\shared\scene_shared;
#using scripts\shared\util_shared;

#insert scripts\shared\shared.gsh;
#insert scripts\shared\version.gsh;

#insert scripts\zm\_zm_utility.gsh;

#using scripts\zm\_load;
#using scripts\zm\_zm;
#using scripts\zm\_zm_audio;
#using scripts\zm\_zm_powerups;
#using scripts\zm\_zm_utility;
#using scripts\zm\_zm_weapons;
#using scripts\zm\_zm_zonemgr;

#using scripts\shared\ai\zombie_utility;

//Perks
#using scripts\zm\_zm_pack_a_punch;
#using scripts\zm\_zm_pack_a_punch_util;
#using scripts\zm\_zm_perk_additionalprimaryweapon;
#using scripts\zm\_zm_perk_doubletap2;
#using scripts\zm\_zm_perk_deadshot;
#using scripts\zm\_zm_perk_juggernaut;
#using scripts\zm\_zm_perk_quick_revive;
#using scripts\zm\_zm_perk_sleight_of_hand;
#using scripts\zm\_zm_perk_staminup;

//Powerups
#using scripts\zm\_zm_powerup_double_points;
#using scripts\zm\_zm_powerup_carpenter;
#using scripts\zm\_zm_powerup_fire_sale;
#using scripts\zm\_zm_powerup_free_perk;
#using scripts\zm\_zm_powerup_full_ammo;
#using scripts\zm\_zm_powerup_insta_kill;
#using scripts\zm\_zm_powerup_nuke;
//#using scripts\zm\_zm_powerup_weapon_minigun;

//Traps
#using scripts\zm\_zm_trap_electric;

#using scripts\zm\zm_usermap;

//*****************************************************************************
// MAIN
//*****************************************************************************

function main()
{
	zm_usermap::main();
	
	level._zombie_custom_add_weapons =&custom_add_weapons;
	
	//Setup the levels Zombie Zone Volumes
	level.zones = [];
	level.zone_manager_init_func =&usermap_test_zone_init;
	init_zones[0] = "start_zone";
	level thread zm_zonemgr::manage_zones( init_zones );

	level.pathdist_type = PATHDIST_ORIGINAL;

	level thread ascenseur_init();
}

//*****************************************************************************
// ASCENSEUR DU BATIMENT 1 (hall du milieu)
// Entites : script_brushmodel "ascenseur_cabine", "ascenseur_porte" (script_int = etage,
// script_vector = glissement d'ouverture), trigger_use "ascenseur_bouton" (dans la cabine)
// et "ascenseur_appel" (script_int = etage, devant chaque porte palliere).
// Un etage = 144 unites, 1,6 s de trajet par etage.
//*****************************************************************************

function ascenseur_init()
{
	cabine = GetEnt( "ascenseur_cabine", "targetname" );
	if ( !isdefined( cabine ) )
	{
		return;
	}
	cabine.etage = 0;
	cabine.en_mouvement = false;
	level.ascenseur_cabine = cabine;

	level.ascenseur_portes = GetEntArray( "ascenseur_porte", "targetname" );
	level.ascenseur_nb_etages = level.ascenseur_portes.size;
	foreach ( porte in level.ascenseur_portes )
	{
		porte.position_fermee = porte.origin;
	}
	ascenseur_ouvrir( 0 );

	bouton = GetEnt( "ascenseur_bouton", "targetname" );
	if ( isdefined( bouton ) )
	{
		bouton EnableLinkTo();
		bouton LinkTo( cabine );
		bouton SetCursorHint( "HINT_NOICON" );
		bouton SetHintString( "Appuyer sur ^3&&1^7 pour changer d'etage" );
		bouton thread ascenseur_bouton_cabine();
	}

	foreach ( appel in GetEntArray( "ascenseur_appel", "targetname" ) )
	{
		appel SetCursorHint( "HINT_NOICON" );
		appel SetHintString( "Appuyer sur ^3&&1^7 pour appeler l'ascenseur" );
		appel thread ascenseur_bouton_appel();
	}
}

function ascenseur_porte( etage )
{
	foreach ( porte in level.ascenseur_portes )
	{
		if ( porte.script_int == etage )
		{
			return porte;
		}
	}
	return undefined;
}

function ascenseur_ouvrir( etage )
{
	porte = ascenseur_porte( etage );
	if ( isdefined( porte ) )
	{
		porte MoveTo( porte.position_fermee + porte.script_vector, 0.6 );
		porte waittill( "movedone" );
	}
}

function ascenseur_fermer( etage )
{
	porte = ascenseur_porte( etage );
	if ( isdefined( porte ) )
	{
		porte MoveTo( porte.position_fermee, 0.6 );
		porte waittill( "movedone" );
	}
}

function ascenseur_aller( etage )
{
	cabine = level.ascenseur_cabine;
	if ( cabine.en_mouvement || etage == cabine.etage )
	{
		return;
	}
	cabine.en_mouvement = true;
	ascenseur_fermer( cabine.etage );
	ecart = etage - cabine.etage;
	duree = Abs( ecart ) * 1.6;
	cabine MoveZ( ecart * 144, duree, duree * 0.2, duree * 0.2 );
	cabine waittill( "movedone" );
	cabine.etage = etage;
	ascenseur_ouvrir( etage );
	cabine.en_mouvement = false;
}

function ascenseur_bouton_cabine()
{
	while ( true )
	{
		self waittill( "trigger", joueur );
		cabine = level.ascenseur_cabine;
		// monte d'un etage a chaque appui, redescend au rez-de-chaussee depuis le dernier
		prochain = cabine.etage + 1;
		if ( prochain >= level.ascenseur_nb_etages )
		{
			prochain = 0;
		}
		ascenseur_aller( prochain );
	}
}

function ascenseur_bouton_appel()
{
	while ( true )
	{
		self waittill( "trigger", joueur );
		ascenseur_aller( self.script_int );
	}
}

function usermap_test_zone_init()
{
	level flag::init( "always_on" );
	level flag::set( "always_on" );
}	

function custom_add_weapons()
{
	zm_weapons::load_weapon_spec_from_table("gamedata/weapons/zm/zm_levelcommon_weapons.csv", 1);
}

