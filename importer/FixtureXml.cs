using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Xml.Serialization;
using Microsoft.Xna.Framework;
using Core.Utilities;

namespace Core.Pipeline
{
    public class FixtureXml : LoadSaver<FixtureXml>
    {
        [XmlAttribute]
        public String Name = String.Empty;

        public XmlVector3 Position = XmlVector3.Zero;
        public XmlVector3 Rotation = XmlVector3.Zero;
        public XmlVector3 Scale = XmlVector3.One;

        public List<FixtureXml> Fixtures = new List<FixtureXml>();

        public FixtureXml()
        {
            CreateOnFileNotExists = false;
        }
    }
}
