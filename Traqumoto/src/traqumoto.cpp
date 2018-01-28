/*
Copyright Maxime LEIBER,
Copyright Manuel MATILDE,
Copyright Antoine SOUSTELLE,
programme crée le 6 mars 2017.

Utilisation des bibliothèques libres suivantes :
Torch
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006           Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
OpenCV
Copyright (C) 2000-2016, Intel Corporation, all rights reserved.
Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
Copyright (C) 2009-2016, NVIDIA Corporation, all rights reserved.
Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
Copyright (C) 2015-2016, OpenCV Foundation, all rights reserved.
Copyright (C) 2015-2016, Itseez Inc., all rights reserved.
Autres
Copyright (c) 2015 Egor Burkov and other contributors

Contact :
leibermaxime@gmail.com
mtld.manu@gmail.com
antoine.soustelle@wanadoo.fr

Ce logiciel est un programme informatique servant à la détection
des deux roues motorisés sur l'autoroute. Le projet a été fait
par commande du Cerema.

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant 
donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.*/

/* Ce fichier se lance via l'executable. Le Main initialise Lua, charge les librairies Lua, y ajoute la fonction getFile et execute le fichier traqumoto.lua */

#include <stdio.h>
#include <stdlib.h>
#include <string>

using namespace std;

extern "C" {	/* charge les librairies Lua */
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lua.h"
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lualib.h"
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lauxlib.h"
}

/* interpreteur */
lua_State* L;

/* La fonction getFile permet de recupérer la vidéo à traiter */
static int getFile(lua_State *L)
{

	FILE *in;
	if (!(in = popen("zenity  --title=\"Select an image\" --file-selection","r")))
	{
    		return 1;
	}

	char buff[512];
	string selectFile = "";
	while (fgets(buff, sizeof(buff), in) != NULL)
	{
		selectFile += buff;
	}
	pclose(in);

	/* push the return */
	lua_pushstring(L, selectFile.c_str());

	/* return the number of results */
	return 1;
}

int main ( int argc, char *argv[] )
{
	/* initialise Lua */
	L = lua_open();

	/* charge les librairies de base de Lua */
	luaL_openlibs(L);

	/* enregistre la fonction getFile dans la librairie Lua */
	lua_register(L, "getFile", getFile);

	/* execute le script */
	luaL_dofile(L, "src/traqumoto.lua");

	/* ferme Lua */
	lua_close(L);

	return 0;
}
