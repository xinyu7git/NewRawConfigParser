#!/usr/bin/python26
# -*- coding: utf-8 -*-
#xinyu7@staff.sina.com.cn
#2013-07-22

from ConfigParser import *

from collections import OrderedDict as _default_dict

import re

DEFAULTSECT = "mysqld"

class NewRawConfigParser(RawConfigParser):
    """docstring for MySQLConfigParser"""
    def __init__(self, defaults=None, dict_type=_default_dict,
                 allow_no_value=False,new_option_len=1):
        RawConfigParser.__init__(self,defaults,dict_type,allow_no_value)
        self._location = _default_dict()
        self._data = [] 
        self._new_option_len = new_option_len

    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        """
        if section in self._sections:
            raise DuplicateSectionError(section)
        self._sections[section] = self._dict({'__name__':section})

        #new add
        linecount = len(self._data)
        if linecount:
            self._data.append('\n')
        else:
            self._data.append("# A new config file")
        self._data.append('[%s]\n'%section)
        self._location[section] = linecount + 1
        #end

    def _read(self, fp, fpname):
        """Parse a sectioned setup file.

        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuations are represented by an embedded newline then
        leading whitespace.  Blank lines, lines beginning with a '#',
        and just about everything else are ignored.
        """
        cursect = None                            # None, or a dictionary
        optname = None
        lineno = 0
        e = None                                  # None, or an exception

        while True:
            line = fp.readline()

            if not line:
                break
            lineno = lineno + 1

            #new add
            self._data.append(line)
            #end 

            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname] = "%s\n%s" % (cursect[optname], value)
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')

                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect 
                    # So sections can't start with a continuation line

                    #new add
                    self._location[sectname] = lineno - 1
                    #end

                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self._optcre.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            if vi in ('=', ':') and ';' in optval:
                                # ';' is a comment delimiter only if it follows
                                # a spacing character
                                pos = optval.find(';')
                                if pos != -1 and optval[pos-1].isspace():
                                    optval = optval[:pos]
                            optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        optname = self.optionxform(optname.rstrip())
                        cursect[optname] = optval

                        #new add
                        if cursect == self._defaults:
                            location_key = DEFAULTSECT + '_' + optname  #KVS
                        else: 
                            location_key = cursect['__name__'] + '_' + optname  #KVS
                        self._location[location_key] = lineno-1 
                        # end

                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

    def set(self, section, option, value=None):
        """Set an option."""
        if not section or section == DEFAULTSECT:
            sectdict = self._defaults
        else:
            try:
                sectdict = self._sections[section]
            except KeyError:
                raise NoSectionError(section)
        #new add
        option = self.optionxform(option)
        spaces = ' '*(self._new_option_len - len(option) - 1)
        add = False

        if not option in sectdict:
            add = True
        if add:
            section_index = self._location[section]
            next_section_index = len(self._data)
            
            # find insert place ,insert new option to the end of its section
            for k,v in self._location.items():
                if k in self._sections or k == DEFAULTSECT:
                    if v > section_index:
                        next_section_index = v
                        break

            insert_index = next_section_index

            for i in range(next_section_index - 1,section_index,-1):
                if not self._data[i] == "\n":
                    break
                else:
                    if not self._data[i - 1] == "\n":
                        insert_index = i 
                        break
            print insert_index

            if value:
                data_value = option + spaces + "= " + str(value) + "\n"
            else:
                data_value = option + "\n"

            self._data.insert(insert_index,data_value) 
            
            for key in self._location:
                if self._location[key] >= insert_index:
                    self._location[key] = self._location[key] + 1

            self._location[section+'_'+option]=insert_index
            self._location = _default_dict(sorted(self._location.items(), key=lambda t: t[1]))

        else:
            # if add is false,modify self._data info.
            location_index = self._location[section + '_' + option]
            data_value = self._data[location_index]
            
            if re.search(r"=", data_value):
                option_format = data_value.split('=')[0]
                value_format = data_value.split('=')[1]
            else:
                option_format = data_value
                value_format = None

            if value:
                if value_format:
                    data_value_new = option_format + "=" + " " + str(value) + "\n"
                else:
                    data_value_new = option + spaces + "=" + " " + str(value) + "\n" 
            else:
                data_value_new = option + "\n"

            self._data[location_index] = data_value_new
        #end

        sectdict[self.optionxform(option)] = value

    def write(self, fp):
        for line in self._data:
            fp.write("%s\n" %str(line).replace("\n", ""))
        fp.close()

    def remove_option(self,section,option):
        """Remove an option. """
        if not section or section == DEFAULTSECT:
            sectdict = self._defaults
        else:
            try:
                sectdict = self._sections[section]
            except KeyError:
                raise NoSectionError(section)
        option = self.optionxform(option)
        existed = option in sectdict
        if existed:
            del sectdict[option]
            ## new add
            location_key = section + '_' + option
            data_index  = self._location[location_key]
            
            del self._location[location_key]
            for key in self._location:
                if self._location[key] > data_index:
                    self._location[key] = self._location[key] -1 
            del self._data[data_index]
            #end

        return existed

    def remove_section(self,section):
        """Remove a file section."""
        existed = section in self._sections
        if existed:
            #new add
            remove_option_list = []
            for option in self._sections[section]:
                if option == '__name__':
                    continue
                remove_option_list.append(option)
            for option in remove_option_list:
                self.remove_option(section,option)
            #end

            del self._sections[section]
            
            #new add
            location_key = section
            data_index = self._location[location_key]
            
            del self._location[location_key]
            for key in self._location:
                if self._location[key] > data_index:
                    self._location[key] = self._location[key] -1 
            del self._data[data_index]
            #end
        return existed




if __name__ == '__main__':
    config = NewRawConfigParser(allow_no_value=True,new_option_len=33)
    # config.read("a.cnf")
    # config.add_section("xinyu7")
    # config.set("xinyu7", "id",1)
    with open("a.cnf",'wb') as configfile:
        config.write(configfile)
    
        
